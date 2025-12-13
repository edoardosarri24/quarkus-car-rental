package org.oristool.eulero;

import org.oristool.eulero.modeling.Activity;
import org.oristool.eulero.modeling.ModelFactory;
import org.oristool.eulero.modeling.Simple;
import org.oristool.eulero.modeling.stochastictime.UniformTime;
import org.oristool.eulero.evaluation.heuristics.SDFHeuristicsVisitor;
import org.checkerframework.checker.units.qual.kN;
import org.oristool.eulero.evaluation.approximator.TruncatedExponentialMixtureApproximation;
import org.oristool.eulero.evaluation.heuristics.AnalysisHeuristicsVisitor;
import org.oristool.eulero.ui.ActivityViewer;
import org.oristool.eulero.evaluation.heuristics.EvaluationResult;
import org.oristool.eulero.modeling.stochastictime.HypoExponentialTime;
import org.oristool.eulero.modeling.stochastictime.HyperExponentialTime;
import org.oristool.eulero.modeling.stochastictime.ErlangTime;
import org.oristool.eulero.modeling.stochastictime.GeneralizeErlangTime;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.List;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.io.IOException;

public class main_correlation0 {

    public static void main(String[] args) {
        System.err.println("executing the workflow analysis...");

        // Simple activities, the block of our model.

        // users
        Activity usersReserve = new Simple(
            "usersReserve",
            new HyperExponentialTime(
                new BigDecimal(5.219857227947522),
                new BigDecimal(1.7278271595714059),
                new BigDecimal(0.7513089162951418)));
        Activity usersStartParallel = new Simple(
            "usersStartParallel",
            new HyperExponentialTime(
                new BigDecimal(11.433503933861681),
                new BigDecimal(0.3877830095882751),
                new BigDecimal(0.9671962104089571)));
        Activity usersReservation = new Simple(
            "usersReservation",
            new HyperExponentialTime(
                new BigDecimal(5.887191235029323),
                new BigDecimal(1.642137628219104),
                new BigDecimal(0.7819011949080112)));
        Activity usersReservationAll = new Simple(
            "usersReservationAll",
            new HyperExponentialTime(
                new BigDecimal(8.553856056295276),
                new BigDecimal(0.20244274612648094),
                new BigDecimal(0.9768803291556827)));
        Activity usersEnd = new Simple(
            "usersEnd",
            new HyperExponentialTime(
                new BigDecimal(0.6867447658996167),
                new BigDecimal(0.21768402873627415),
                new BigDecimal(0.7593132482873786)));

        // start-choice
        Activity startChoiceFirstChoice = new Simple(
            "startChoiceFirstChoice",
            new GeneralizeErlangTime(
                5,
                new BigDecimal(18.08985733436383),
                new BigDecimal(10.128603925903818)));
        Activity startChoiceSecondChoice = new Simple(
            "startChoiceSecondChoice",
            new HyperExponentialTime(
                new BigDecimal(4.558083918738367),
                new BigDecimal(0.260110589834814),
                new BigDecimal(0.9460149254306794)));
        Activity startChoiceThirdChoice = new Simple(
            "startChoiceThirdChoice",
            new GeneralizeErlangTime(
                7,
                new BigDecimal(24.278223896520384),
                new BigDecimal(11.530603615053302)));
        Activity startChoiceEnd = new Simple(
            "startChoiceEnd",
            new HyperExponentialTime(
                new BigDecimal(11.644695233915417),
                new BigDecimal(0.7052833721514669),
                new BigDecimal(0.9428919357151762)));

        // first-choice
        Activity firstChoice = new Simple(
            "firstChoice",
            new HyperExponentialTime(
                new BigDecimal(0.5152155704010831),
                new BigDecimal(0.253736027767757),
                new BigDecimal(0.6700234080116396)));

        // second-choice
        Activity secondChoice = new Simple(
            "secondChoice",
            new HyperExponentialTime(
                new BigDecimal(0.5290321211041311),
                new BigDecimal(0.2879776936437056),
                new BigDecimal(0.6475223572037656)));

        // third-choice
        Activity thirdChoice = new Simple(
            "thirdChoice",
            new HyperExponentialTime(
                new BigDecimal(0.469050565164904),
                new BigDecimal(0.3625081906800484),
                new BigDecimal(0.5640618439382538)));

        // start-parallel
        Activity startParallel = new Simple(
            "startParallel",
            new HyperExponentialTime(
                new BigDecimal(0.20413909408095815),
                new BigDecimal(0.1774290783338817),
                new BigDecimal(0.5350003193112729)));
        Activity startParallelEnd = new Simple(
            "startParallelEnd",
            new HyperExponentialTime(
                new BigDecimal(14.913909885245317),
                new BigDecimal(0.6883207640213228),
                new BigDecimal(0.9558831823798428)));

        // first-parallel
        Activity firstParallel = new Simple(
            "firstParallel",
            new HyperExponentialTime(
                new BigDecimal(0.5955794082595988),
                new BigDecimal(0.3095707706162428),
                new BigDecimal(0.6579896045530073)));

        // second-parallel
        Activity secondParallel = new Simple(
            "secondParallel",
            new HyperExponentialTime(
                new BigDecimal(0.5791842770245158),
                new BigDecimal(0.30096874565445303),
                new BigDecimal(0.6580495233222305)));

        // reservation
        Activity reservation = new Simple(
            "reservation",
            new HyperExponentialTime(
                new BigDecimal(0.8433174019931315),
                new BigDecimal(0.3648960169186765),
                new BigDecimal(0.6979871178327712)));
        Activity reservationAll = new Simple(
            "reservationAll",
            new HyperExponentialTime(
                new BigDecimal(0.39296824706096484),
                new BigDecimal(0.22173687357697314),
                new BigDecimal(0.6392792802069784)));

        // Model of the workflow.
        Activity model = ModelFactory.sequence(
            usersReserve,
            ModelFactory.XOR(List.of(0.2, 0.5, 0.3),
                ModelFactory.sequence(startChoiceFirstChoice, firstChoice),
                ModelFactory.sequence(startChoiceSecondChoice, secondChoice),
                ModelFactory.sequence(startChoiceThirdChoice, thirdChoice)),
            startChoiceEnd,
            usersStartParallel,
            startParallel,
            ModelFactory.forkJoin(firstParallel, secondParallel),
            startParallelEnd,
            usersReservation,
            reservation,
            usersReservationAll,
            reservationAll,
            usersEnd
        );

        // Analyze the model.
        AnalysisHeuristicsVisitor analyzer = new SDFHeuristicsVisitor(
            BigInteger.valueOf(2),
            BigInteger.valueOf(5),
            new TruncatedExponentialMixtureApproximation());
        double fairTimeTick = model.getLeastExpectedTimeTick();
        BigDecimal timeStep = BigDecimal.valueOf(fairTimeTick);
        //double fairTimeLimit = model.getFairTimeLimit();
        double fairTimeLimit = 170;
        double[] cdf = model.analyze(BigDecimal.valueOf(fairTimeLimit), timeStep, analyzer);

        // Save cdf to a CSV file
        try (PrintWriter writer = new PrintWriter(new FileWriter("../eulero_CDF.csv"))) {
            writer.println("time,cdf");
            for (int i = 0; i < cdf.length; i++) {
                double time = i * timeStep.doubleValue();
                writer.println(time + "," + cdf[i]);
            }
            System.out.println("CDF saved");
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

}